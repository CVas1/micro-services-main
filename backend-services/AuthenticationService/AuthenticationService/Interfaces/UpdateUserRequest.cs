using System.ComponentModel.DataAnnotations;

namespace AuthenticationService.Interfaces;

public class UpdateUserRequest
{
    [Required] public string JwToken { get; set; }
}