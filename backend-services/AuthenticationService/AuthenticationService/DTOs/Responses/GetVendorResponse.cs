using System.ComponentModel.DataAnnotations;
using AuthenticationService.Interfaces;

namespace AuthenticationService.DTOs.Responses;

public class GetVendorResponse : IGetUserResponse
{
    [MaxLength(100)] public string? BusinessName { get; set; }

    [MaxLength(255)] public string? Address { get; set; }

    [MaxLength(20)] public string? PhoneNumber { get; set; }
}