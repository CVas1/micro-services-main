using System.ComponentModel.DataAnnotations;
using AuthenticationService.Enums;

namespace AuthenticationService.DTOs.Requests;

public class RegisterRequest
{
    [Required] [EmailAddress] public string Email { get; set; }

    [Required]
    [MinLength(8)]
    [MaxLength(16)]
    public string Password { get; set; }

    [Required]
    [EnumDataType(typeof(UserType))]
    public UserType UserType { get; set; }
}