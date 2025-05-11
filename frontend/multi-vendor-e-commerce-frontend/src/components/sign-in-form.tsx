import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { SignInFormProps } from "@/types.ts";
import { SignInImage } from "@/components/sign-in-image.tsx";
import { useNavigate } from "react-router";
import getAuthAxiosInstance from "@/requests/authAxiosInstance.ts";
import { AxiosError } from "axios";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";
import { AlertCircle } from "lucide-react";
import { Check } from "lucide-react"
import { useEffect, useState } from "react";


const signUpFormSchema = z.object({
    email: z.string().email("Invalid email"),
    password: z
        .string()
        .min(8, "Password must be at least 8 characters long.")
        .max(16, "Password must be at most 16 characters long.")
        .regex(/[A-Z]/, "Password must contain at least one uppercase letter.")
        .regex(/[a-z]/, "Password must contain at least one lowercase letter.")
        .regex(/[0-9]/, "Password must contain at least one digit.")
        .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character."),
});

const signInFormSchema = z.object({
    email: z.string().email("Invalid email"),
    password: z.string().min(1, "Password is required"),
});

export function SignInForm({ type }: SignInFormProps) {
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [signUpSuccess, setSignUpSuccess] = useState(false);
    const [signInSuccess, setSignInSuccess] = useState(false);
    const [confirmEmail, setConfirmEmail] = useState('');
    const [userEmail, setUserEmail] = useState('');
    const [userToken, setUserToken] = useState('')
    const navigate = useNavigate();
    const formSchema = type === "sign-in" ? signInFormSchema : signUpFormSchema;
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: { email: "", password: "" },
    });

    async function onSubmitSignUp(values: z.infer<typeof formSchema>) {
        const axios = await getAuthAxiosInstance();
        try {
            const response = await axios?.post('/register', {
                email: values.email,
                password: values.password,
                userType: 'Customer',
            });
            if (response?.status === 200) {
                console.log(response.data);
                setSignUpSuccess(true);
                setUserEmail(values.email);
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                setErrorMessage(problemDetails.detail);
            } else {
                setErrorMessage("An unexpected error occurred.")
            }

        }
    }

    async function onSubmitConfirmEmail(email: string, token: string) {
        const axios = await getAuthAxiosInstance();

        try {
            const response = await axios?.post('/confirm-email', {
                email,
                token,
            });

            if (response?.status === 200) {
                console.log('Email confirmed:', response.data);
                setTimeout(() => navigate("/dashboard", { state: { email, token } }), 1000);
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                setErrorMessage(problemDetails.detail);
            } else {
                setErrorMessage("An unexpected error occurred while confirming email.");
            }
        }
    }

    const handleConfirmClick = () => {
        onSubmitConfirmEmail(userEmail, confirmEmail);
    };

    async function onSubmitSignIn(values: z.infer<typeof formSchema>) {
        const axios = await getAuthAxiosInstance();
        try {
            const response = await axios?.post('/authenticate', {
                email: values.email,
                password: values.password,
            });
            if (response?.status === 200) {
                const token = response.data.jwToken;
                const email = values.email;

                setUserToken(token);
                setUserEmail(email);
                setSignInSuccess(true);

                setTimeout(() => {
                    navigate("/dashboard", { state: { userEmail: email, userToken: token } });
                }, 1000);
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                setErrorMessage(problemDetails.detail);
            } else {
                setErrorMessage("An unexpected error occurred.")
            }
        }
    }

    useEffect(() => {
        if (errorMessage) {
            const timer = setTimeout(() => setErrorMessage(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [errorMessage]);

    return (
        <div /* Container */ className="min-h-screen flex">
            <Alert variant="destructive"
                className={`fixed top-2 left-1/3 max-w-1/3 flex flex-col items-center transition-opacity duration-500 ${errorMessage ? "opacity-100 visible" : "opacity-0 invisible"}`}>
                <div className="flex flex-row gap-2">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                </div>
                <AlertDescription>
                    {errorMessage}
                </AlertDescription>
            </Alert>

            <Alert variant="default"
                className={`fixed top-2 left-1/3 max-w-1/3 flex flex-col items-center transition-opacity duration-500 ${signInSuccess ? "opacity-100 visible" : "opacity-0 invisible"} bg-violet-500 text-black`}>
                <div className="flex flex-row gap-2">
                    <Check className="h-4 w-4" />
                    <AlertTitle>Success</AlertTitle>
                </div>
                <AlertDescription className="text-black">
                    Signed In successfully
                </AlertDescription>
            </Alert>


            <div /* Content */ className="w-1/2 flex justify-center items-center bg-primary-900 text-white">
                <div className="relative max-w-md w-full bg-white text-gray-900 shadow-lg rounded-lg p-8">
                    <div
                        className={`absolute inset-0 text-center flex flex-col items-center gap-2 bg-violet-900 text-gray-50 dark:bg-violet-900 dark:text-gray-50 duration-500 transition-opacity  ${signUpSuccess ? "visible opacity-100" : "invisible opacity-0"}`}>
                        <h1 className='font-bold mt-5'>We sent you a confirmation email.</h1>
                        <Input className="mt-2 w-100 h-12 text-base px-4 placeholder:text-white" type="email" placeholder="Token" onChange={(e) => setConfirmEmail(e.target.value)} />
                        <Button onClick={handleConfirmClick} className="mt-2 shadow-sm active:shadow-lg transition duration-100">Confirm</Button>
                        <p className="mt-2">Back to <a href={"/"}
                            className="underline underline-offset-2 cursor-pointer text-violet-50">Homepage</a>
                        </p>
                    </div>
                    <h1 className="text-2xl font-extrabold text-center">
                        {type === "sign-in" ? "Sign In" : "Sign Up"}
                    </h1>
                    <div className="mt-6">
                        <Form {...form}>
                            <form className="space-y-6"
                                onSubmit={type === 'sign-up' ? form.handleSubmit(onSubmitSignUp) : form.handleSubmit(onSubmitSignIn)}>
                                <FormField
                                    control={form.control}
                                    name="email"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Email</FormLabel>
                                            <FormControl>
                                                <Input
                                                    className="w-full px-4 py-3 rounded-lg bg-gray-100 border border-gray-300 text-sm focus:outline-none focus:border-gray-500 focus:bg-white"
                                                    placeholder="Enter your email"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="password"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Password</FormLabel>
                                            <FormControl>
                                                <Input
                                                    className="w-full px-4 py-3 rounded-lg bg-gray-100 border border-gray-300 text-sm focus:outline-none focus:border-gray-500 focus:bg-white"
                                                    type="password"
                                                    placeholder="Enter your password"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <Button
                                    className="w-full dark:bg-gray-900 dark:text-gray-50 dark:hover:bg-gray-950 bg-violet-400 text-gray-50 hover:bg-violet-500 rounded-lg transition-all duration-300 cursor-pointer"
                                    type="submit"
                                >
                                    {type === "sign-in" ? "Sign In" : "Sign Up"}
                                </Button>
                                {type === "sign-up" && (<p className='text-center'>Already have an account? <a
                                    className='underline decoration-dotted underline-offset-2 hover:cursor-pointer'
                                    onClick={() => {
                                        navigate('/sign-in')
                                    }}>Sign in</a></p>)}
                                {type === "sign-in" && (<p className='text-center'>Don't have an account? <a
                                    className='underline decoration-dotted underline-offset-2 hover:cursor-pointer'
                                    onClick={() => {
                                        navigate('/sign-up')
                                    }}>Sign Up</a></p>)}
                            </form>
                        </Form>
                    </div>
                </div>
            </div>

            {/* Right Section: Image */}
            <div className="w-1/2 h-screen">
                <SignInImage />
            </div>
        </div>
    );
}