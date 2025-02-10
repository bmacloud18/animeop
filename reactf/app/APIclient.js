import HTTPclient from './HTTPclient.js';

const API_BASE = "/api/";

export default {
    getVideos: async(query) => {
        return HTTPclient.get('videos', API_BASE)
    }
}