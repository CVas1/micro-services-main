using AuthenticationService.DTOs.Requests;
using AuthenticationService.DTOs.Responses;
using AuthenticationService.Enums;
using AuthenticationService.Interfaces.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using RegisterRequest = AuthenticationService.DTOs.Requests.RegisterRequest;

namespace AuthenticationService.Controllers;

[ApiController]
[Route("[controller]")]
public class AuthenticationController(IAccountService accountService, ITokenService tokenService) : ControllerBase
{
    [HttpPost("/register")]
    public async Task<IActionResult> Register([FromBody] RegisterRequest registerRequest)
    {
        var status = await accountService.RegisterAsync(registerRequest);
        return status switch
        {
            RegistrationOutcomes.EmailAlreadyExists => StatusCode(StatusCodes.Status409Conflict,
                new ProblemDetails { Detail = "Email already exists." }),
            RegistrationOutcomes.SystemError => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "User generation failed possibly due to invalid password." }),
            RegistrationOutcomes.EmailCantBeSend => StatusCode(StatusCodes.Status400BadRequest,
                new ProblemDetails { Detail = "Email cant be sent possibly due to invalid email." }),
            RegistrationOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }

    [HttpPost("/authenticate")]
    public async Task<IActionResult> Login([FromBody] AuthenticationRequest authenticationRequest)
    {
        var (status, response) = await accountService.AuthenticateAsync(authenticationRequest);
        return status switch
        {
            AuthenticationOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found" }),
            AuthenticationOutcomes.WrongPassword => StatusCode(StatusCodes.Status401Unauthorized,
                new ProblemDetails { Detail = "Wrong password" }),
            AuthenticationOutcomes.Success => Ok(response),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }

    [HttpPost("/confirm-email")]
    public async Task<IActionResult> ConfirmEmail([FromBody] ConfirmEmailRequest confirmEmailRequest)
    {
        var status = await accountService.ConfirmEmailAsync(confirmEmailRequest);
        return status switch
        {
            ConfirmEmailOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found." }),
            ConfirmEmailOutcomes.InvalidToken => StatusCode(StatusCodes.Status401Unauthorized,
                new ProblemDetails { Detail = "Invalid reset token" }),
            ConfirmEmailOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }

    [HttpPost("/request-password-reset")]
    public async Task<IActionResult> RequestPasswordReset([FromBody] PasswordResetRequest passwordResetRequest)
    {
        var status = await accountService.RequestPasswordReset(passwordResetRequest);
        return status switch
        {
            RequestPasswordResetOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found." }),
            RequestPasswordResetOutcomes.EmailCantBeSend => StatusCode(StatusCodes.Status400BadRequest,
                new ProblemDetails { Detail = "Email cant be sent possibly due to invalid email." }),
            RequestPasswordResetOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }

    [HttpPost("/confirm-password-reset")]
    public async Task<IActionResult> ConfirmPasswordReset(
        [FromBody] ConfirmPasswordResetRequest confirmPasswordResetRequest)
    {
        var status = await accountService.ConfirmPasswordReset(confirmPasswordResetRequest);
        return status switch
        {
            ConfirmPasswordResetOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found." }),
            ConfirmPasswordResetOutcomes.UnsupportedPasswordFormat => StatusCode(StatusCodes.Status400BadRequest,
                new ProblemDetails
                    { Detail = "Password could not be reset due to invalid password format or invalid token." }),
            ConfirmPasswordResetOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }

    [HttpPost("/refresh-token")]
    public async Task<IActionResult> RefreshToken([FromBody] RefreshTokenRequest refreshTokenRequest)
    {
        var (status, response) = await tokenService.RefreshTokenAsync(refreshTokenRequest);
        return status switch
        {
            RefreshTokenOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found. This token belongs to no user." }),
            RefreshTokenOutcomes.Expired => StatusCode(StatusCodes.Status401Unauthorized,
                new ProblemDetails { Detail = "Token is expired." }),
            RefreshTokenOutcomes.Success => Ok(response),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    [Authorize(Roles = "Customer")]
    [HttpPost("/customer-policy")]
    public  IActionResult CheckForCustomerPolicy([FromBody] CheckForPolicyRequest request)
    {
        var status = accountService.CheckForCustomerPolicy(request);
        return status switch
        {
            CheckForPolicyOutcomes.Failure => StatusCode(StatusCodes.Status401Unauthorized, 
                new ProblemDetails { Detail = "Does not belong to customer policy."}),
            CheckForPolicyOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    [Authorize(Roles = "Vendor")]
    [HttpPost("/vendor-policy")]
    public  IActionResult CheckForVendorPolicy([FromBody] CheckForPolicyRequest request)
    {
        var status = accountService.CheckForVendorPolicy(request);
        return status switch
        {
            CheckForPolicyOutcomes.Failure => StatusCode(StatusCodes.Status401Unauthorized, 
                new ProblemDetails { Detail = "Does not belong to vendor policy."}),
            CheckForPolicyOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    [Authorize(Roles = "Admin")]
    [HttpPost("/admin-policy")]
    public  IActionResult CheckForAdminPolicy([FromBody] CheckForPolicyRequest request)
    {
        var status = accountService.CheckForAdminPolicy(request);
        return status switch
        {
            CheckForPolicyOutcomes.Failure => StatusCode(StatusCodes.Status401Unauthorized, 
                new ProblemDetails { Detail = "Does not belong to admin policy."}),
            CheckForPolicyOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    [Authorize(Roles = "Admin")]
    [HttpGet("/user/{email}")]
    public async Task<IActionResult> GetUserInfo([FromRoute] string email)
    {
        var (status, response) = await accountService.GetUserInfo(email);
        return status switch
        {
            GetUserInfoOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found. There is no such user" }),
            GetUserInfoOutcomes.UserIsAdmin => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Admin users don't have user details." }),
            GetUserInfoOutcomes.CustomerNotInitialized => StatusCode(StatusCodes.Status404NotFound, new ProblemDetails
                { Detail = "Customer is not initialized due to unknown reason." }),
            GetUserInfoOutcomes.VendorNotInitialized => StatusCode(StatusCodes.Status404NotFound, new ProblemDetails
                { Detail = "Vendor is not initialized due to unknown reason." }),
            GetUserInfoOutcomes.Success => Ok(response),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    [Authorize(Roles = "Customer")]
    [HttpPut("/customer/{email}")]
    public async Task<IActionResult> UpdateCustomerInfo([FromRoute] string email, [FromBody] UpdateCustomerRequest request)
    {
        var status = await accountService.UpdateCustomerInfo(email, request, "Customer");
        return status switch
        {
            UpdateUserInfoOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found. There is no such user" }),
            UpdateUserInfoOutcomes.UserIsAdmin => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Admin users don't have user details." }),
            UpdateUserInfoOutcomes.InvalidToken => StatusCode(StatusCodes.Status401Unauthorized,
                new ProblemDetails { Detail = "Invalid json web token" }),
            UpdateUserInfoOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
    
    [HttpPut("/vendor/{email}")]
    public async Task<IActionResult> UpdateVendorInfo([FromRoute] string email, [FromBody] UpdateVendorRequest request)
    {
        var status = await accountService.UpdateCustomerInfo(email, request, "Vendor");
        return status switch
        {
            UpdateUserInfoOutcomes.EmailNotFound => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Email not found. There is no such user" }),
            UpdateUserInfoOutcomes.UserIsAdmin => StatusCode(StatusCodes.Status404NotFound,
                new ProblemDetails { Detail = "Admin users don't have user details." }),
            UpdateUserInfoOutcomes.WrongUserType => StatusCode(StatusCodes.Status403Forbidden,
                new ProblemDetails { Detail = "A customer can't be updated with vendor info and vice versa"}),
            UpdateUserInfoOutcomes.InvalidToken => StatusCode(StatusCodes.Status401Unauthorized,
                new ProblemDetails { Detail = "Invalid json web token" }),
            UpdateUserInfoOutcomes.Success => Ok(),
            _ => StatusCode(StatusCodes.Status500InternalServerError,
                new ProblemDetails { Detail = "Unexpected error." })
        };
    }
}