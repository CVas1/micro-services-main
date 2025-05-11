using AuthenticationService.Contexts;
using AuthenticationService.Entities;
using AuthenticationService.Interfaces.Repositories;
using Microsoft.EntityFrameworkCore;

namespace AuthenticationService.Repositories;

public class VendorRepository(UserDbContext dbContext) : GenericRepository<Vendor>(dbContext), IVendorRepository
{
    private readonly DbSet<Vendor> _vendors = dbContext.Set<Vendor>();
}