import { ConsumerUi } from "@/components/consumer-ui";
import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export default function LandingPage() {
    return (

        
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <ConsumerUi></ConsumerUi>
        </ThemeProvider>
    );
}