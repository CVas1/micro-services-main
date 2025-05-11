using System.ComponentModel.DataAnnotations;
using AuthenticationService.DTOs;
using AuthenticationService.Enums;
using Microsoft.AspNetCore.Identity;

namespace AuthenticationService.Entities;

public class User : IdentityUser
{
    public List<RefreshToken> RefreshTokens { get; set; } = new List<RefreshToken>();

    public bool OwnsToken(string token)
    {
        return this.RefreshTokens?.Find(x => x.Token == token) != null;
    }

    public Vendor? Vendor { get; set; }
    public Customer? Customer { get; set; }
}