import {OrderUi} from "@/components/order-ui";
import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export default function OrderPage() {
    return (

        
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <OrderUi></OrderUi>
        </ThemeProvider>
    );
}