using AuthenticationService.Contexts;
using AuthenticationService.ServiceRegistration;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend",
        policy =>
        {
            policy.WithOrigins("http://localhost:5173") // Allow frontend URL
                .AllowAnyHeader()
                .AllowAnyMethod()
                .AllowCredentials();
            policy.WithOrigins("https://localhost:5173") // Allow frontend URL
                .AllowAnyHeader()
                .AllowAnyMethod()
                .AllowCredentials();
        });
});


// Add json files
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
builder.Configuration.AddJsonFile("appsettings.Development.json", optional: true, reloadOnChange: true);

// Add services to the container.
builder.Services.AddServices(builder.Configuration);

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseCors("AllowFrontend");

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    try
    {
        var db = services.GetRequiredService<UserDbContext>();
        
        // First check if the database exists and has any tables
        if (db.Database.GetPendingMigrations().Any())
        {
            Console.WriteLine("Applying pending migrations...");
            db.Database.Migrate();
            Console.WriteLine("Migrations applied successfully.");
        }
        else
        {
            Console.WriteLine("Database is up to date, no migrations needed.");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Failed to apply migrations: {ex.Message}");
        throw;
    }
}

app.Run();