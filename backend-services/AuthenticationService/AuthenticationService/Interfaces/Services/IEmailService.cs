using AuthenticationService.DTOs;

namespace AuthenticationService.Interfaces.Services;

public interface IEmailService
{
    public Task SendEmailAsync(Email request);
}