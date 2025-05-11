using AuthenticationService.DTOs.Responses;
using AuthenticationService.DTOs;
using AuthenticationService.DTOs.Requests;
using AuthenticationService.Entities;
using AuthenticationService.Enums;

namespace AuthenticationService.Interfaces.Services;

public interface ITokenService
{
    RefreshToken GenerateRefreshToken();
    Task<string> GenerateJwToken(User user);
    Task<(RefreshTokenOutcomes, RefreshResponse?)> RefreshTokenAsync(RefreshTokenRequest refreshTokenRequest);
    bool IsTokenValid(string token);
}