using System.Text.Json.Serialization;

namespace AuthenticationService.Enums;

[JsonConverter(typeof(JsonStringEnumConverter<UserType>))]
public enum UserType
{
    Customer,
    Vendor
}