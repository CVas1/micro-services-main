# Use official .NET SDK image to build the project
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy the project files
COPY . ./

# Restore dependencies
RUN dotnet restore

# Build the project
RUN dotnet publish -c Release -o /out

# Use ASP.NET runtime image (smaller and more secure)
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy build artifacts
COPY --from=build /out ./

# Expose the port your app runs on
EXPOSE 8080

# Run the application
CMD ["dotnet", "AuthenticationService.dll"]
