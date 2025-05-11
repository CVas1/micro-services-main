namespace AuthenticationService.DTOs.Responses;

public class AuthenticationResponse
{
    public string JwToken { get; set; }
    public string RefreshToken { get; set; }
}