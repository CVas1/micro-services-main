import axios, {AxiosInstance} from 'axios';
import {Config} from "@/types.ts";


let instance: AxiosInstance | null = null

export default async function getOrderAxiosInstance() {
    if (!instance) {
        const configResponse = await axios.get('/config.json')
        const config : Config = configResponse.data;
        if (!config) {
            return null;
        }
        const url = config.ORDER_URL;
        instance = axios.create({
            baseURL: url,
            timeout: 5000,
        });
    }
    return instance;
}




