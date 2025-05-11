using AuthenticationService.DTOs;
using AuthenticationService.Entities;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace AuthenticationService.Contexts;

public class UserDbContext(DbContextOptions<UserDbContext> options) : IdentityDbContext<User>(options)
{
    public DbSet<Vendor> Vendors { get; set; }
    public DbSet<Customer> Customers { get; set; }

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);
        builder.Entity<User>().ToTable("Users");
        builder.Entity<User>()
            .HasOne(u => u.Vendor)
            .WithOne(v => v.User)
            .HasForeignKey<Vendor>(v => v.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.Entity<User>()
            .HasOne(u => u.Customer)
            .WithOne(c => c.User)
            .HasForeignKey<Customer>(c => c.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.Entity<RefreshToken>().ToTable("RefreshTokens");
        SeedRoles(builder);
    }

    private void SeedRoles(ModelBuilder builder)
    {
        builder.Entity<IdentityRole>().HasData(
            new IdentityRole() { Name = "Admin", ConcurrencyStamp = "1", NormalizedName = "ADMIN" },
            new IdentityRole() { Name = "Vendor", ConcurrencyStamp = "2", NormalizedName = "VENDOR" },
            new IdentityRole() { Name = "Customer", ConcurrencyStamp = "3", NormalizedName = "CUSTOMER" });
    }
}