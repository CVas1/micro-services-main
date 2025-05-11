using AuthenticationService.DTOs.Requests;
using AuthenticationService.DTOs.Responses;
using AuthenticationService.Entities;
using AutoMapper;

namespace AuthenticationService.Mappings;

public class GeneralProfile : Profile
{
    public GeneralProfile()
    {
        CreateMap<Vendor, GetVendorResponse>();
        CreateMap<Customer, GetCustomerResponse>();
        CreateMap<UpdateCustomerRequest, Customer>();
        CreateMap<UpdateVendorRequest, Vendor>();
    }
}