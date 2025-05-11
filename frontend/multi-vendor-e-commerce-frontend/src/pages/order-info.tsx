import {OrderInfo} from "@/components/order-info";
import {ModeToggle} from "@/components/mode-toggle.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";

export default function OrderInfoPage() {
    return (

        
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <ModeToggle/>
            <OrderInfo></OrderInfo>
        </ThemeProvider>
    );
}