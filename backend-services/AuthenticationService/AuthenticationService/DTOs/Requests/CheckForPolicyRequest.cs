using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.DTOs.Requests;

public class CheckForPolicyRequest
{
    [Required]
    public string Token { get; set; }
}