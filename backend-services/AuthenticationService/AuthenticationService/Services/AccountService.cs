using System.Diagnostics;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using AuthenticationService.Contexts;
using AuthenticationService.DTOs;
using AuthenticationService.DTOs.Requests;
using AuthenticationService.DTOs.Responses;
using AuthenticationService.Entities;
using AuthenticationService.Enums;
using AuthenticationService.Interfaces;
using AuthenticationService.Interfaces.Repositories;
using AuthenticationService.Interfaces.Services;
using AuthenticationService.Settings;
using AutoMapper;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.Extensions.Options;
using Microsoft.OpenApi.Extensions;


namespace AuthenticationService.Services;

public class AccountService(
    UserManager<User> userManager,
    SignInManager<User> signInManager,
    ITokenService tokenService,
    UserDbContext dbContext,
    IEmailService emailService,
    IOptions<AppRootSettings> appRootOptions,
    ICustomerRepository customerRepository,
    IVendorRepository vendorRepository,
    IMapper mapper,
    ILogger<AccountService> logger)
    : IAccountService
{
    private readonly AppRootSettings _appRootSettings = appRootOptions.Value;

    public async Task<RegistrationOutcomes> RegisterAsync(RegisterRequest request)
    {
        var userWithSameEmail = await userManager.FindByEmailAsync(request.Email);
        if (userWithSameEmail != null)
        {
            return RegistrationOutcomes.EmailAlreadyExists;
        }

        var user = new User()
        {
            Email = request.Email,
            UserName = request.Email,
        };

        var result = await userManager.CreateAsync(user, request.Password);
        if (!result.Succeeded)
        {
            return RegistrationOutcomes.SystemError;
        }

        var userType = request.UserType;

        var role = userType == UserType.Customer ? Roles.Customer : Roles.Vendor;
        await userManager.AddToRoleAsync(user, role.ToString());

        if (userType == UserType.Customer)
        {
            var customer = new Customer()
            {
                UserId = user.Id,
                FullName = "",
                Address = "",
                PhoneNumber = ""
            };
            await dbContext.Customers.AddAsync(customer);
        }
        else
        {
            var vendor = new Vendor()
            {
                UserId = user.Id,
                BusinessName = "",
                Address = "",
                PhoneNumber = ""
            };
            await dbContext.Vendors.AddAsync(vendor);
        }

        await dbContext.SaveChangesAsync();

        var confirmationCode = await GenerateEmailConfirmationTokenAsync(user);
        // For now, I will be sending the token row, but later it will be wrapped inside a frontend url
        var email = new Email()
        {
            Subject = "EMAIL CONFIRMATION",
            Body = $@"<h1>Welcome to our service!</h1>
                       <p>This is your email confirmation code [{confirmationCode}], confirm before it expires!</p>
                       <p>If you didn't request this, please ignore this email.</p>",
            To = user.Email,
        };

        try
        {
            await emailService.SendEmailAsync(email);
        }
        catch (Exception e)
        {
            // if an error occurs after user creation, delete the user. customer or vendor should be deleted as well
            // due to cascade
            await userManager.DeleteAsync(user);
            await dbContext.SaveChangesAsync();
            return RegistrationOutcomes.EmailCantBeSend;
        }


        return RegistrationOutcomes.Success;
    }

    public async Task<(AuthenticationOutcomes, AuthenticationResponse?)> AuthenticateAsync(
        AuthenticationRequest request)
    {
        var user = await userManager.FindByEmailAsync(request.Email);
        if (user == null)
        {
            return (AuthenticationOutcomes.EmailNotFound, null);
        }

        var result = await signInManager.PasswordSignInAsync(user, request.Password, false, false);
        if (!result.Succeeded)
        {
            return (AuthenticationOutcomes.WrongPassword, null);
        }

        var jwSecurityToken = await tokenService.GenerateJwToken(user);
        var refreshToken = tokenService.GenerateRefreshToken();
        user.RefreshTokens.Add(refreshToken);
        await userManager.UpdateAsync(user);
        await dbContext.SaveChangesAsync();
        var response = new AuthenticationResponse()
        {
            RefreshToken = refreshToken.Token,
            JwToken = jwSecurityToken,
        };
        return (AuthenticationOutcomes.Success, response);
    }

    public async Task<string> GenerateEmailConfirmationTokenAsync(User user)
    {
        var confirmationToken = await userManager.GenerateEmailConfirmationTokenAsync(user);

        var tokenBytes = Encoding.UTF8.GetBytes(confirmationToken);
        var encodedToken = WebEncoders.Base64UrlEncode(tokenBytes);

        return encodedToken;
    }

    public async Task<ConfirmEmailOutcomes> ConfirmEmailAsync(ConfirmEmailRequest request)
    {
        var user = await userManager.FindByEmailAsync(request.Email);
        if (user == null)
        {
            return ConfirmEmailOutcomes.EmailNotFound;
        }

        var tokenBytes = WebEncoders.Base64UrlDecode(request.Token);
        var decodedToken = Encoding.UTF8.GetString(tokenBytes);

        var result = await userManager.ConfirmEmailAsync(user, decodedToken);
        return result.Succeeded ? ConfirmEmailOutcomes.Success : ConfirmEmailOutcomes.InvalidToken;
    }

    public async Task<RequestPasswordResetOutcomes> RequestPasswordReset(PasswordResetRequest request)
    {
        var user = await userManager.FindByEmailAsync(request.Email);
        if (user == null)
        {
            return RequestPasswordResetOutcomes.EmailNotFound;
        }

        var resetCode = await userManager.GeneratePasswordResetTokenAsync(user);
        var encodedResetCode = Uri.EscapeDataString(resetCode);
        Debug.Assert(user.Email != null, "user.Email != null");
        var email = new Email()
        {
            Subject = "RESET YOUR PASSWORD",
            Body = $@"<p>This is your password reset code [{encodedResetCode}]</p>
                       <p>If you didn't request this, please ignore this email.</p>",
            To = user.Email
        };

        try
        {
            await emailService.SendEmailAsync(email);
        }
        catch (Exception ex)
        {
            return RequestPasswordResetOutcomes.EmailCantBeSend;
        }

        return RequestPasswordResetOutcomes.Success;
    }

    public async Task<ConfirmPasswordResetOutcomes> ConfirmPasswordReset(ConfirmPasswordResetRequest request)
    {
        var user = await userManager.FindByEmailAsync(request.Email);
        if (user == null)
        {
            return ConfirmPasswordResetOutcomes.EmailNotFound;
        }

        var decodedResetCode = Uri.UnescapeDataString(request.Token);

        var resetPasswordResult = await userManager.ResetPasswordAsync(user, decodedResetCode, request.Password);
        return resetPasswordResult.Succeeded
            ? ConfirmPasswordResetOutcomes.Success
            : ConfirmPasswordResetOutcomes.UnsupportedPasswordFormat;
    }

    public IList<string> GetUserRoles(string jwToken)
    {
        var handler = new JwtSecurityTokenHandler();
        var token = handler.ReadJwtToken(jwToken);
        var roles = token.Claims.Where(c => c.Type == ClaimTypes.Role || c.Type == "role").Select(c => c.Value)
            .ToList();
        return roles;
    }
    
    public string? GetUserEmailFromToken(string jwToken)
    {
        var handler = new JwtSecurityTokenHandler();
        var token = handler.ReadJwtToken(jwToken);
        var emailClaim = token.Claims.FirstOrDefault(c => c.Type == "email");

        return emailClaim?.Value;
    }

    public CheckForPolicyOutcomes CheckForPolicy(CheckForPolicyRequest request, Roles requiredRole)
    {
        var isValid = tokenService.IsTokenValid(request.Token);
        if (!isValid)
        {
            return CheckForPolicyOutcomes.Failure;
        }
        
        var email = GetUserEmailFromToken(request.Token);
        if (string.IsNullOrEmpty(email))
        {
            return CheckForPolicyOutcomes.EmailNotConfirmed;
        }
        
        var user = userManager.FindByEmailAsync(email).Result;
        if ((user == null || !user.EmailConfirmed) && requiredRole != Roles.Admin)
        {
            return CheckForPolicyOutcomes.EmailNotConfirmed;
        }

        var roles = GetUserRoles(request.Token);
        foreach (var role in roles)
        {
            if (role == requiredRole.ToString())
            {
                return CheckForPolicyOutcomes.Success;
            }
        }

        return CheckForPolicyOutcomes.Failure;
    }

    public CheckForPolicyOutcomes CheckForCustomerPolicy(CheckForPolicyRequest request)
    {
        return CheckForPolicy(request, Roles.Customer);
    }

    public CheckForPolicyOutcomes CheckForVendorPolicy(CheckForPolicyRequest request)
    {
        return CheckForPolicy(request, Roles.Vendor);
    }

    public CheckForPolicyOutcomes CheckForAdminPolicy(CheckForPolicyRequest request)
    {
        return CheckForPolicy(request, Roles.Admin);
    }

    public async Task<(GetUserInfoOutcomes, IGetUserResponse?)> GetUserInfo(string email)
    {
        var user = await userManager.FindByEmailAsync(email);
        if (user == null)
        {
            return (GetUserInfoOutcomes.EmailNotFound, null);
        }
    
        var roles = await userManager.GetRolesAsync(user);
        var role = roles.FirstOrDefault();
        switch (role){
            case nameof(Roles.Admin): return (GetUserInfoOutcomes.UserIsAdmin, null);
            case nameof(Roles.Customer):
                var customer = await customerRepository.GetByIdAsync(user.Id);
                return customer == null
                    ? (GetUserInfoOutcomes.CustomerNotInitialized, null)
                    : (GetUserInfoOutcomes.Success, mapper.Map<GetCustomerResponse>(customer));
            case nameof(Roles.Vendor):
                var vendor = await vendorRepository.GetByIdAsync(user.Id);
                return vendor == null
                    ? (GetUserInfoOutcomes.VendorNotInitialized, null)
                    : (GetUserInfoOutcomes.Success, mapper.Map<GetVendorResponse>(vendor));
            default: return (GetUserInfoOutcomes.UnknownError, null);
        }
    }

    public async Task<UpdateUserInfoOutcomes> UpdateCustomerInfo(string email, UpdateUserRequest request, string expectedRole)
    {
        var isValid = tokenService.IsTokenValid(request.JwToken);
        if (!isValid)
        {
            return UpdateUserInfoOutcomes.InvalidToken;
        }
        var user = await userManager.FindByEmailAsync(email);
        if (user == null)
        {
            return UpdateUserInfoOutcomes.EmailNotFound;
        }
        
        var roles = await userManager.GetRolesAsync(user);
        var role = roles.FirstOrDefault();

        if (role != expectedRole)
        {
            return UpdateUserInfoOutcomes.WrongUserType;
        }
        
        switch (role)
        {
            case nameof(Roles.Admin): return UpdateUserInfoOutcomes.UserIsAdmin;
            case nameof(Roles.Customer):
                var customer = mapper.Map<UpdateCustomerRequest, Customer>((UpdateCustomerRequest) request);
                customer.UserId = user.Id;
                customer.User = user;
                await customerRepository.UpdateAsync(customer);
                return UpdateUserInfoOutcomes.Success;
            case nameof(Roles.Vendor):
                var vendor = mapper.Map<UpdateVendorRequest, Vendor>((UpdateVendorRequest) request);
                vendor.UserId = user.Id;
                vendor.User = user;
                await vendorRepository.UpdateAsync(vendor);
                return UpdateUserInfoOutcomes.Success;
            default: return UpdateUserInfoOutcomes.UnknownError;
        }
    }
}