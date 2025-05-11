using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AuthenticationService.Entities;

public class Customer
{
    [Key] public string UserId { get; set; } = null!;

    [MaxLength(50)] public string? FullName { get; set; }

    [MaxLength(255)] public string? Address { get; set; }

    [MaxLength(20)] public string? PhoneNumber { get; set; }

    [ForeignKey("UserId")] public User User { get; set; } = null!;
}