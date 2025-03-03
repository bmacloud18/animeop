FROM node:20 AS base
SHELL ["/bin/bash", "-c"]
WORKDIR /reactf
ENV NEXT_TELEMETRY_DISABLED 1

# Install dependencies, run dev server.
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000

ENV PORT 3000
CMD ["npm", "run", "start"]
