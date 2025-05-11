using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.DTOs.Requests;

public class ConfirmEmailRequest
{
    [Required] [EmailAddress] public string Email { get; set; }

    [Required] public string Token { get; set; }
}