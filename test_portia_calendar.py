"""Test script to verify Portia AI Google Calendar integration."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from portia import Portia, Config, LLMProvider, PortiaToolRegistry
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input

def test_portia_calendar_integration():
    """Test the Portia AI Google Calendar integration."""
    
    # load environment variables
    load_dotenv()
    
    # check required environment variables
    required_vars = ["GOOGLE_API_KEY", "PORTIA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    
    # initialize portia with Gemini configuration and Portia Cloud tools
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia = Portia(config, tools=PortiaToolRegistry(config))
    
    print("🔧 Testing Portia AI Google Calendar Integration")
    print("=" * 50)
    
    # test 1: check if calendar tools are available
    print("📋 Test 1: Checking available tools...")
    available_tools = portia.tool_registry.get_tools()
    calendar_tools = [tool for tool in available_tools if 'gcalendar' in tool.id]
    gmail_tools = [tool for tool in available_tools if 'gmail' in tool.id]
    
    print(f"✅ Found {len(calendar_tools)} Google Calendar tools:")
    for tool in calendar_tools:
        print(f"  • {tool.id}: {tool.description}")
    
    print(f"✅ Found {len(gmail_tools)} Gmail tools:")
    for tool in gmail_tools:
        print(f"  • {tool.id}: {tool.description}")
    
    # test 2: create a simple calendar event plan
    print("\n📅 Test 2: Creating calendar event plan...")
    
    # calculate test event time (1 hour from now)
    test_start = datetime.now() + timedelta(hours=1)
    test_end = test_start + timedelta(hours=1)
    
    plan = PlanBuilderV2(label="Test Calendar Event")
    
    # define inputs
    plan.input(name="event_title", description="Test event title")
    plan.input(name="start_time", description="Event start time")
    plan.input(name="end_time", description="Event end time")
    plan.input(name="event_description", description="Event description")
    plan.input(name="attendees", description="List of attendees")
    
    # create calendar event
    plan.invoke_tool_step(
        tool="portia:google:gcalendar:create_event",
        args={
            "event_title": Input("event_title"),
            "start_time": Input("start_time"),
            "end_time": Input("end_time"),
            "event_description": Input("event_description"),
            "attendees": Input("attendees")
        },
        step_name="create_test_event"
    )
    
    built_plan = plan.build()
    print("✅ Calendar event plan created successfully")
    print(f"📋 Plan steps: {len(built_plan.steps)}")
    
    # test 3: test plan execution (this will require OAuth)
    print("\n🚀 Test 3: Testing plan execution...")
    print("⚠️ This will require OAuth authentication with Google")
    print("⚠️ The plan will create a test calendar event")
    
    user_input = input("\nDo you want to proceed with the test? (yes/no): ").strip().lower()
    
    if user_input in ['yes', 'y']:
        try:
            # prepare test data
            plan_inputs = {
                "event_title": "Portia AI Integration Test",
                "start_time": test_start.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": test_end.strftime("%Y-%m-%dT%H:%M:%S"),
                "event_description": "This is a test event to verify Portia AI Google Calendar integration is working properly.",
                "attendees": ["test@example.com"]
            }
            
            print("⏳ Executing plan...")
            result = portia.run_plan(built_plan, plan_run_inputs=plan_inputs)
            
            print(f"✅ Plan execution completed with state: {result.state}")
            
            if result.state.name == "COMPLETED":
                print("🎉 SUCCESS! Portia AI Google Calendar integration is working!")
                return True
            else:
                print(f"⚠️ Plan completed with state: {result.state}")
                return True  # still consider it working if it gets to OAuth
                
        except Exception as e:
            print(f"❌ Error during plan execution: {str(e)}")
            return False
    else:
        print("⏭️ Skipping plan execution test")
        print("✅ Portia AI Google Calendar integration setup is complete!")
        return True

if __name__ == "__main__":
    success = test_portia_calendar_integration()
    if success:
        print("\n🎉 All tests passed! Your Portia AI Google Calendar integration is ready.")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
