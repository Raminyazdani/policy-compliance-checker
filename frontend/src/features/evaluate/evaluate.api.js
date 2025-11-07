import { http } from '../../api/http'
export const evaluateApi = { run: () => http('GET','/evaluate') }
