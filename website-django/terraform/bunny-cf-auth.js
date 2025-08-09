import * as BunnySDK from "https://esm.sh/@bunny.net/edgescript-sdk@0.11.2";
import * as jose from "https://esm.sh/jose@5.9.6";

const AUD = "45b0c2e70d653b89645875ae5978416d7628146a61adb292b1066c18fd52c0ff"
const TEAM_DOMAIN = 'https://taska.cloudflareaccess.com';
const CERTS_URL = `${TEAM_DOMAIN}/cdn-cgi/access/certs`;
const JWKS = jose.createRemoteJWKSet(new URL(CERTS_URL));


/**
 * When a response is not served from the cache, you can use this event handler
 * to modify the request going to the origin.
 *
 * @param {Context} context - The context of the middleware.
 * @param {Request} context.request - The current request.
 */
async function onOriginRequest(context: { request: Request }): Promise<Response> | Response | Promise<Request> | Request | void {
  // Check if request contains Authorization header.
  const token = context.request.headers.get('cf-access-jwt-assertion');
  if (token) {
    const result = await jose.jwtVerify(token, JWKS, {
        issuer: TEAM_DOMAIN,
        audience: AUD,
    });
  }
  else //Deny request
  {
    return new Response('Unauthorized', { status: 401 });
  }
}

/**
 * When a response is not served from the cache, you can use this event handler
 * to modify the response going from the origin.
 * This modify the response before being cached.
 *
 * Returns an HTTP response.
 * @param {Context} context - The context of the middleware.
 * @param {Request} request - The current request done to the origin.
 * @param {Response} response - The HTTP response or string.
 */
async function onOriginResponse(context: { request: Request, response: Response }): Promise<Response> | Response | void {
  // context.response.headers.append("After", "Added on the response return.");
}

BunnySDK.net.http.servePullZone()
  .onOriginRequest(onOriginRequest)
  .onOriginResponse(onOriginResponse);
