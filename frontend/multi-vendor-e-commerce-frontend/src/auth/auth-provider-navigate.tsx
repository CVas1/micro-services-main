import { Auth0Provider } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";

const Auth0ProviderWithNavigate = ({ children }: any) => {
    const navigate = useNavigate();

    const domain = process.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = process.meta.env.VITE_AUTH0_CLIENT_ID;

    if (!domain || !clientId) return null;

    return (
        <Auth0Provider
            domain={domain}
            clientId={clientId}
            authorizationParams={{
                redirect_uri: window.location.origin,
                audience: "my-secure-api",
                scope: "openid profile email"
            }}
            onRedirectCallback={(appState) => {
                navigate(appState?.returnTo || "/");
            }}
        >
            {children}
        </Auth0Provider>
    );
};

export default Auth0ProviderWithNavigate;