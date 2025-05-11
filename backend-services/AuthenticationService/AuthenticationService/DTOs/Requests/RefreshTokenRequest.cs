using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.DTOs.Requests;

public class RefreshTokenRequest
{
    [Required] public string RefreshToken { get; set; }
}