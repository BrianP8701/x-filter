# Design

## UX
I initially proposed we have our interface in X where we create a bot account on X and allow users to interact with their x_filter by messaging the bot. We could do this, but we also could just do a CLI based interface. i think we should do a CLI interface to make this as easy as possible. but what do u think?

## Database
We use sqlite in a key value style for development speed

## Backend
its super simple rn. a single route for message events to come. copilot conversates with the user to confirm what it should do and then it runs.

later we can add scheduling, allowing a user to have multiple scehduled things and potentially using x dms instead of cli
