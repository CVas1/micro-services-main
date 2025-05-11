namespace AuthenticationService.DTOs.Responses;

public class RefreshResponse
{
    public required string RefreshToken { get; set; }
    public required string JwToken { get; set; }
}