using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.DTOs.Requests;

public class PasswordResetRequest
{
    [Required] [EmailAddress] public string Email { get; set; }
}