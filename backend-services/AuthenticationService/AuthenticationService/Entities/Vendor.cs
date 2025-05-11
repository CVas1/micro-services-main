using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AuthenticationService.Entities;

public class Vendor
{
    [Key] public string UserId { get; set; } = null!;

    [MaxLength(100)] public string? BusinessName { get; set; }

    [MaxLength(20)] public string? PhoneNumber { get; set; }

    [MaxLength(255)] public string? Address { get; set; }

    [ForeignKey("UserId")] public User User { get; set; } = null!;
}