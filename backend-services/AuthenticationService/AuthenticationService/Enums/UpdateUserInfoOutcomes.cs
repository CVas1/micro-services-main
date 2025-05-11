namespace AuthenticationService.Enums;

public enum UpdateUserInfoOutcomes
{
    Success, InvalidToken, EmailNotFound, UserIsAdmin, UnknownError, WrongUserType
}