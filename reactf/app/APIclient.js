import HTTPclient from './HTTPclient.js';

const API_BASE = "/api/";

export default {
    getVideos: async(query, history) => {
        return HTTPclient.get(`videos?query=${query}&history=${history.join(',')}`, API_BASE)
    },

    getToken: async() => {
        return HTTPclient.post('inconspicuousroute', {}, API_BASE)
    }
}