using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using AuthenticationService.Contexts;
using AuthenticationService.DTOs;
using AuthenticationService.DTOs.Requests;
using AuthenticationService.Entities;
using AuthenticationService.Interfaces.Services;
using AuthenticationService.Settings;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using AuthenticationService.DTOs.Responses;
using AuthenticationService.Enums;
using Microsoft.Extensions.Options;

namespace AuthenticationService.Services;

public class TokenService(UserManager<User> userManager, IOptions<JwtSettings> jwtSettings, UserDbContext userDbContext)
    : ITokenService
{
    private readonly JwtSettings _jwtSettings = jwtSettings.Value;

    public RefreshToken GenerateRefreshToken()
    {
        var randomBytes = new byte[64];
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(randomBytes);
        }

        return new RefreshToken
        {
            Token = Convert.ToBase64String(randomBytes),
            Expires = DateTime.UtcNow.AddDays(7),
            Created = DateTime.UtcNow
        };
    }

    public async Task<string> GenerateJwToken(User user)
    {
        var roles = await userManager.GetRolesAsync(user);
        var roleClaims = roles.Select(role => new Claim(ClaimTypes.Role, role)).ToList();
        var claims = new[]
        {
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(JwtRegisteredClaimNames.Email, user.Email),
            new Claim("uid", user.Id),
        }.Union(roleClaims);

        var symmetricSecurityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtSettings.Key));
        var signingCredentials = new SigningCredentials(symmetricSecurityKey, SecurityAlgorithms.HmacSha256);

        var jwtSecurityToken = new JwtSecurityToken(
            issuer: _jwtSettings.Issuer,
            audience: _jwtSettings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_jwtSettings.DurationInMinutes),
            signingCredentials: signingCredentials);

        string token = new JwtSecurityTokenHandler().WriteToken(jwtSecurityToken);
        return token;
    }

    public async Task<(RefreshTokenOutcomes, RefreshResponse?)> RefreshTokenAsync(
        RefreshTokenRequest refreshTokenRequest)
    {
        var refreshToken = refreshTokenRequest.RefreshToken;
        var user = await userDbContext.Users
            .Include(u => u.RefreshTokens)
            .FirstOrDefaultAsync(u => u.RefreshTokens
                .Any(t => t.Token == refreshToken));

        if (user == null)
        {
            return (RefreshTokenOutcomes.EmailNotFound, null);
        }

        var existingToken =
            user.RefreshTokens.FirstOrDefault(t => t.Token == refreshToken && t.Revoked == null && !t.IsExpired);
        if (existingToken is { IsActive: false })
        {
            return (RefreshTokenOutcomes.Expired, null);
        }

        if (existingToken != null) existingToken.Revoked = DateTime.UtcNow;
        await userManager.UpdateAsync(user);
        await userDbContext.SaveChangesAsync();

        string newToken = await GenerateJwToken(user);
        var newRefreshToken = GenerateRefreshToken();
        user.RefreshTokens.Add(newRefreshToken);
        await userManager.UpdateAsync(user);
        await userDbContext.SaveChangesAsync();

        var response = new RefreshResponse()
        {
            JwToken = newToken,
            RefreshToken = newRefreshToken.Token
        };

        return (RefreshTokenOutcomes.Success, response);
    }
    
    public bool IsTokenValid(string token)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        try
        {
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtSettings.Key)),
                ValidateIssuer = true,
                ValidIssuer = _jwtSettings.Issuer,
                ValidateAudience = true,
                ValidAudience = _jwtSettings.Audience,
                ValidateLifetime = true,
            };
            
            // This will throw an exception if token is invalid
            tokenHandler.ValidateToken(token, validationParameters, out SecurityToken validatedToken);
            return true;
        }
        catch
        {
            return false;
        }
    }
}