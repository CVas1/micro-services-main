import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useNavigate } from 'react-router-dom';


export function LandingUi() {

    const navigate = useNavigate();
    const handleSignIn = () => {
        navigate('/sign-in'); // This will route to the sign-in page
    };
    const handleSignUp = () => {
        navigate('/sign-up'); // This will route to the sign-in page
    };


    return (
        <div /* Container */ className="min-h-screen flex-col ">
            <div /* Content */ className="h-20 w-1/1 flex ">
                <div /* logo-div */ className="w-1/2 content-center items-center flex">
                    <img
                        src="src\assets\landing-page\shop-svgrepo-com.svg"
                        alt="Description of image"
                        className="w-10 h-10 ml-60"
                    />
                    <p className="text-2xl ml-1 mb-1 italic font-bold">Shoply</p>
                </div>
                <div /* Button-div */ className="w-1/2 items-center content-center flex">
                    <Button className="px-9 py-4 w-30 h-11 text-lg ml-143 rounded-3xl" onClick={handleSignIn}>Sign In</Button>
                </div>
            </div>
            <div /* Information */ className=" flex w-1/1 h-1/2">
                <div /* sign-up-div */ className="w-1/2 flex-col pt-25">
                    <p className="ml-60 text-6xl font-100 max-w-xl">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                    <p className="ml-60 mt-5 text-xl font-50 max-w-md">Ullamcorper a lacus vestibulum sed. Scelerisque eleifend donec.</p>
                    <div className="ml-60 mt-5 flex items-center space-x-2 relative">
                        <Input
                            type="email"
                            placeholder="Enter your email address"
                            className="w-150 h-12 placeholder:text-base placeholder:font-200 border-2 border-gray-300 rounded-3xl"
                        />
                        <Button className="absolute mr-30 top-1/2 right-1 transform -translate-y-1/2 h-10 px-4 text-sm rounded-3xl" onClick={handleSignUp}>Sign Up</Button>
                    </div>
                    <p className="ml-60 mt-5 text-lg font-50 max-w-md">Quis varius quam quisque id diam. Aliquam sem et tortor consequat id porta nibh venenatis cras.</p>
                </div>
                <div /* Image-div */ className="w-1/2  pt-18">
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/60a52584834d6d460eebd0cb77b4ab23.png?originalWidth=1392&originalHeight=1095"
                        alt="Description of image"
                        className="w-150 h-120 ml-35"
                    />
                </div>
            </div>
            <div /* bottom-info */ className="w-1/1 h-1/2 flex-col mt-3">
                <div className="flex">
                    <p className="ml-60 mt-5 text-2xl font-200">Discover a world of products at your fingertips at Shoply.</p>
                </div>
                <div className="flex">
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/4a6ab9bbbf33ac29cf1747e48492a14e.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-70"
                    />
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/d7d665c21caba6bf4e58aea093f60a0c.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-8"
                    />
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/ea0fba11cd0b0a8221a77893385d4b6c.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-8"
                    />
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/bb1480775c17a84b2787e71d4b8b5c72.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-8"
                    />
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/2075ad1e1e60e6fa121f54a1bfe4185c.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-8"
                    />
                    <img
                        src="https://cdn.shopify.com/b/shopify-brochure2-assets/f000a563db2c785b97ea90a1a2695c1e.svg"
                        alt="Description of image"
                        className="w-50 h-50 ml-8"
                    />
                </div>
            </div>
        </div>
    );
}