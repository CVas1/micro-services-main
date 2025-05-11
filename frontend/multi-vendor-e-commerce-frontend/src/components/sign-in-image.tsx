import signInImage from './../assets/signup-illustration.svg';

export function SignInImage() {
    return (
        <img
            alt="Sign In Illustration"
            src={signInImage}
            className="w-full h-full object-cover bg-gray-950"
        />
    );
}
