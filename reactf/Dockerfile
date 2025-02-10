FROM node:20 AS base
SHELL ["/bin/bash", "-c"]
WORKDIR /reactf
ENV NEXT_TELEMETRY_DISABLED 1

# Install dependencies, run dev server. 
FROM base AS dev-runner
COPY package.json package-lock.json ./
RUN npm install
COPY . .
EXPOSE 3000

ENV PORT 3000
CMD ["npm", "run", "dev"]
