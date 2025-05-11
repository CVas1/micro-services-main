using System.Reflection;
using AuthenticationService.Contexts;
using AuthenticationService.Entities;
using AuthenticationService.Interfaces.Repositories;
using AuthenticationService.Interfaces.Services;
using AuthenticationService.Repositories;
using AuthenticationService.Services;
using AuthenticationService.Settings;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace AuthenticationService.ServiceRegistration;

public static class ServiceRegistration
{
    public static void AddServices(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<UserDbContext>(options =>
        {
            options.UseNpgsql(configuration.GetConnectionString("DefaultConnection"),
                npgsqlOptions =>
                {
                    npgsqlOptions.EnableRetryOnFailure(
                        maxRetryCount: 10,
                        maxRetryDelay: TimeSpan.FromSeconds(30),
                        errorCodesToAdd: null);
                });
        });
        services.AddIdentity<User, IdentityRole>().AddEntityFrameworkStores<UserDbContext>()
            .AddDefaultTokenProviders();
        services.AddLogging(configure => configure.AddConsole())
            .Configure<LoggerFilterOptions>(options => options.MinLevel = LogLevel.Information);
        services.AddAutoMapper(Assembly.GetExecutingAssembly());

        services.Configure<MailSettings>(configuration.GetSection("MailSettings"));
        services.Configure<JwtSettings>(configuration.GetSection("JwtSettings"));
        services.Configure<AppRootSettings>(configuration.GetSection("AppRootSettings"));

        services.AddScoped<IAccountService, AccountService>();
        services.AddScoped<ITokenService, TokenService>();
        services.AddScoped<IEmailService, EmailService>();

        services.AddScoped<ICustomerRepository, CustomerRepository>();
        services.AddScoped<IVendorRepository, VendorRepository>();
    }
}