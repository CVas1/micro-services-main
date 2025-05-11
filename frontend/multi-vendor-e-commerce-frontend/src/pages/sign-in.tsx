import {SignInForm} from "@/components/sign-in-form.tsx";

import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export default function SignInPage() {
    return (
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <SignInForm type={"sign-in"}></SignInForm>
        </ThemeProvider>
    );
}