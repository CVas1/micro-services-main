using AuthenticationService.Contexts;
using AuthenticationService.Interfaces.Repositories;
using Microsoft.EntityFrameworkCore;

namespace AuthenticationService.Repositories;

public class GenericRepository<T>(UserDbContext dbContext) : IGenericRepository<T> where T : class
{
    public virtual async Task<T?> GetByIdAsync(string id)
    {
        return await dbContext.Set<T>().FindAsync(id);
    }

    public async Task<T> CreateAsync(T entity)
    {
        await dbContext.Set<T>().AddAsync(entity);
        await dbContext.SaveChangesAsync();
        return entity;
    }

    public async Task UpdateAsync(T entity)
    {
        dbContext.Entry(entity).State = EntityState.Modified;
        await dbContext.SaveChangesAsync();
    }

    public async Task DeleteAsync(T entity)
    {
        dbContext.Set<T>().Remove(entity);
        await dbContext.SaveChangesAsync();
    }
}