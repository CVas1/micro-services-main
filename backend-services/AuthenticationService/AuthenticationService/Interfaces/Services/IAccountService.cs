using AuthenticationService.DTOs.Requests;
using AuthenticationService.DTOs.Responses;
using AuthenticationService.Entities;
using AuthenticationService.Enums;

namespace AuthenticationService.Interfaces.Services;

public interface IAccountService
{
    public Task<RegistrationOutcomes> RegisterAsync(RegisterRequest request);
    public Task<(AuthenticationOutcomes, AuthenticationResponse?)> AuthenticateAsync(AuthenticationRequest request);
    public Task<ConfirmEmailOutcomes> ConfirmEmailAsync(ConfirmEmailRequest request);
    public Task<RequestPasswordResetOutcomes> RequestPasswordReset(PasswordResetRequest request);

    public Task<ConfirmPasswordResetOutcomes> ConfirmPasswordReset(ConfirmPasswordResetRequest request);

    public IList<string> GetUserRoles(string jwToken);

    public CheckForPolicyOutcomes CheckForPolicy(CheckForPolicyRequest request, Roles requiredRole);

    public CheckForPolicyOutcomes CheckForCustomerPolicy(CheckForPolicyRequest request);

    public CheckForPolicyOutcomes CheckForVendorPolicy(CheckForPolicyRequest request);

    public CheckForPolicyOutcomes CheckForAdminPolicy(CheckForPolicyRequest request);

    public Task<(GetUserInfoOutcomes, IGetUserResponse?)> GetUserInfo(string email);

    public Task<UpdateUserInfoOutcomes> UpdateCustomerInfo(string email, UpdateUserRequest request, string expectedRole);
}