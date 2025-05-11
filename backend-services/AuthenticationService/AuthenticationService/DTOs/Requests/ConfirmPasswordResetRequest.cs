using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.DTOs.Requests;

public class ConfirmPasswordResetRequest
{
    [Required] [EmailAddress] public string Email { get; set; }
    [Required] public string Token { get; set; }

    [Required]
    [MinLength(8)]
    [MaxLength(16)]
    public string Password { get; set; }
}