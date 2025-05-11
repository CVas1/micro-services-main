import {LandingUi} from "@/components/landing-ui";

import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export default function LandingPage() {
    return (

        
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <LandingUi></LandingUi>
        </ThemeProvider>
    );
}