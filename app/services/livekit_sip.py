import os
import logging
from livekit.api import LiveKitAPI
from livekit.protocol.sip import (
    CreateSIPInboundTrunkRequest, 
    SIPInboundTrunkInfo, 
    ListSIPInboundTrunkRequest,
    DeleteSIPTrunkRequest
)

logger = logging.getLogger(__name__)

async def create_sip_inbound_trunk(name: str, number: str) -> None:
    """
    Creates a SIP inbound trunk in LiveKit for the given number.
    
    Args:
        name: The name of the trunk (usually the agent's name).
        number: The phone number in E.164 format (e.g., +1234567890).
    """
    
    api_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([api_url, api_key, api_secret]):
        logger.error("LiveKit credentials not set. Cannot create SIP trunk.")
        return

    try:
        async with LiveKitAPI(api_url, api_key, api_secret) as api:
            # Check if trunk already exists? 
            # The SDK doesn't have a simple "get by number", so we might just try to create it.
            # If it fails because of duplicate number, we catch the error.
            
            logger.info(f"Creating SIP inbound trunk for {name} with number {number}")
            
            trunk_info = SIPInboundTrunkInfo(
                name=f"agent-{name}-trunk",
                numbers=[number],
                # You might want to restrict allowed_numbers or allowed_addresses here for security
                # but for now we keep it open or rely on defaults.
                # If using Twilio, you might not strictly need auth if you rely on IP allowlisting, 
                # but LiveKit usually requires some configuration.
                # For "Open" trunks (testing), you might need:
                # allowed_addresses=["0.0.0.0/0"] # BE CAREFUL with this in prod!
            )
            
            request = CreateSIPInboundTrunkRequest(trunk=trunk_info)
            
            result = await api.sip.create_inbound_trunk(request)
            logger.info(f"Successfully created SIP inbound trunk: {result.sip_trunk_id}")
            
    except Exception as e:
        logger.error(f"Failed to create SIP inbound trunk: {e}")
        # We don't raise here to avoid blocking the agent update, 
        # but in a real app you might want to notify the user.

async def delete_sip_inbound_trunk_by_number(number: str) -> None:
    """
    Deletes the SIP inbound trunk associated with the given number.
    
    Args:
        number: The phone number to search for and delete the trunk of.
    """
    api_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([api_url, api_key, api_secret]):
        logger.error("LiveKit credentials not set. Cannot delete SIP trunk.")
        return

    try:
        async with LiveKitAPI(api_url, api_key, api_secret) as api:
            # List all inbound trunks to find the one with the matching number
            # Pagination might be needed if there are many trunks, but for now we list default page size
            list_request = ListSIPInboundTrunkRequest()
            trunks_list = await api.sip.list_sip_inbound_trunk(list_request)
            
            target_trunk_id = None
            for trunk in trunks_list.items:
                if number in trunk.numbers:
                    target_trunk_id = trunk.sip_trunk_id
                    break
            
            if target_trunk_id:
                logger.info(f"Found trunk {target_trunk_id} for number {number}. Deleting...")
                delete_request = DeleteSIPTrunkRequest(sip_trunk_id=target_trunk_id)
                await api.sip.delete_sip_trunk(delete_request)
                logger.info(f"Successfully deleted SIP inbound trunk: {target_trunk_id}")
            else:
                logger.warning(f"No SIP trunk found containing number: {number}")

    except Exception as e:
        logger.error(f"Failed to delete SIP inbound trunk for number {number}: {e}")


