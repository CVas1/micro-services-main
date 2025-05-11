import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

// const PrivateRoute = ({ children }: any) => {
//     const { isAuthenticated, isLoading } = useAuth0();

//     if (isLoading) return <div>Loading...</div>;
//     return isAuthenticated ? children : <Navigate to="/sign-in" replace />;
// };

interface ProtectedRouteProps {
    component: React.ComponentType<any>;
    role?: string;
    [key: string]: any;
}

const PrivateRoute: React.FC<ProtectedRouteProps> = ({
    component: Component,
    role,
    ...rest
}) => {
    const { user, isAuthenticated, isLoading } = useAuth0();
    const roles = user?.["http://schemas.auth0.com/roles"] || [];

    if (isLoading) return <p>Loading...</p>;

    if (!isAuthenticated) {
        return <Navigate to="/sign-in" />;
    }

    if (role && !roles.includes(role)) {
        return <Navigate to="/unauthorized" />;
    }

    return <Component {...rest} />;
};

export default PrivateRoute;