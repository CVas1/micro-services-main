import {SignInForm} from "@/components/sign-in-form.tsx";
import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";






export default function SignUpPage() {
    return (

        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <SignInForm type={"sign-up"}></SignInForm>
        </ThemeProvider>
    );
}