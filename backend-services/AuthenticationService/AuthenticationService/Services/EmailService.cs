using AuthenticationService.DTOs;
using AuthenticationService.Interfaces.Services;
using AuthenticationService.Settings;
using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;

namespace AuthenticationService.Services;

public class EmailService(IOptions<MailSettings> mailSettings, ILogger<EmailService> logger) : IEmailService
{
    private readonly MailSettings _mailSettings = mailSettings.Value;

    public async Task SendEmailAsync(Email request)
    {
        if (string.IsNullOrEmpty(request.To))
        {
            logger.LogError("To is not present.");
            throw new Exception("Invalid email address.");
        }

        try
        {
            logger.LogInformation($"Email Request - To: {request.To}, Subject: {request.Subject}");
            logger.LogInformation($"Email Body: {request.Body}");

            var email = new MimeMessage();

            var senderEmail = request.From;
            if (senderEmail == null)
            {
                senderEmail = _mailSettings.EmailFrom;
            }

            logger.LogInformation($"Email Sender - From: {senderEmail}");
            email.Sender = new MailboxAddress(_mailSettings.DisplayName, senderEmail);
            email.From.Add(new MailboxAddress(_mailSettings.DisplayName, senderEmail));

            email.To.Add(MailboxAddress.Parse(request.To));
            email.Subject = request.Subject;

            var builder = new BodyBuilder()
            {
                HtmlBody = request.Body,
                TextBody = request.Body
            };
            email.Body = builder.ToMessageBody();

            using var smtp = new SmtpClient();
            await smtp.ConnectAsync(_mailSettings.SmtpHost, _mailSettings.SmtpPort, SecureSocketOptions.StartTls);
            await smtp.AuthenticateAsync(_mailSettings.SmtpUser, _mailSettings.SmtpPass);
            await smtp.SendAsync(email);
            await smtp.DisconnectAsync(true);

            logger.LogInformation("Email sent successfully");
        }
        catch (ArgumentNullException ex)
        {
            logger.LogError($"Null argument error: {ex.ParamName} - {ex.Message}");
            throw;
        }
        catch (System.Exception ex)
        {
            logger.LogError($"Email sending failed: {ex.GetType().Name} - {ex.Message}");
            logger.LogError($"Stack trace: {ex.StackTrace}");
            throw new Exception($"Email sending failed: {ex.Message}");
        }
    }
}