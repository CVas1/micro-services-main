using AuthenticationService.Contexts;
using AuthenticationService.Entities;
using AuthenticationService.Interfaces.Repositories;
using Microsoft.EntityFrameworkCore;

namespace AuthenticationService.Repositories;

public class CustomerRepository(UserDbContext dbContext) : GenericRepository<Customer>(dbContext), ICustomerRepository
{
    private readonly DbSet<Customer> _customers = dbContext.Set<Customer>();
}