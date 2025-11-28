#include <tgbot/tgbot.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <set>
#include <ctime>
#include <cstdlib>
#include <map>

// Logging utility
void logInfo(const std::string& message) {
    std::cout << "[INFO] " << message << std::endl;
}

void logError(const std::string& message) {
    std::cerr << "[ERROR] " << message << std::endl;
}

void logWarning(const std::string& message) {
    std::cerr << "[WARNING] " << message << std::endl;
}

// Global set to store subscribed member IDs
std::set<int64_t> subscribedMembers;

// Global map to store subscription preferences (chat_id -> subscription type)
// "daily" = daily messages, "weekly" = weekly messages, "both" = daily + weekly
std::map<int64_t, std::string> subscriptionPreferences;

// Array of motivational quotes
const std::vector<std::string> motivationalQuotes = {
    "🌟 You are capable of amazing things! Keep pushing forward!",
    "💪 Every day is a new opportunity to become a better version of yourself!",
    "🚀 Don't watch the clock; do what it does. Keep going!",
    "✨ Your potential is limitless. Believe in yourself!",
    "🎯 Success is the sum of small efforts repeated day in and day out!",
    "🌈 The only way to do great work is to love what you do!",
    "💫 You've got this! Keep moving forward with confidence!",
    "🏆 Champions aren't made in the gyms. They are made from something they have deep inside them - a desire!",
    "🔥 Don't let yesterday take up too much of today. Focus on the present!",
    "⭐ You are destined for greatness. Start believing it today!",
    "🌻 Every challenge is an opportunity to grow stronger!",
    "💎 Your determination will define your destiny!",
    "🎪 Life is 10% what happens to you and 90% how you react to it!",
    "🌙 The future belongs to those who believe in the beauty of their dreams!",
    "🎨 You are a work of art in progress. Keep creating!"
};

// Array of weekly deep insights
const std::vector<std::string> weeklyInsights = {
    "📚 <b>Weekly Wisdom:</b>\n\nReflect on your progress this week. Every step forward, no matter how small, is a victory worth celebrating! 🎉",
    "🔮 <b>Weekly Insight:</b>\n\nSuccess is not a destination, it's a journey. Enjoy the process, learn from setbacks, and keep growing! 🌱",
    "💡 <b>Weekly Thought:</b>\n\nThis week, focus on progress over perfection. Consistency beats intensity every single time! 💯",
    "🎯 <b>Weekly Challenge:</b>\n\nTake on one challenge this week that scares you a little. Growth happens outside comfort zones! 🚀",
    "🌟 <b>Weekly Reminder:</b>\n\nYou are stronger than you think. You have overcome 100% of your bad days so far! 💪",
    "✨ <b>Weekly Message:</b>\n\nBe kind to yourself this week. You're doing better than you think, and your efforts matter! 💝",
    "🏅 <b>Weekly Boost:</b>\n\nCelebrate your wins this week, big or small. You've earned it! Take time to appreciate your progress! 🎊"
};

std::string getRandomMotivation() {
    srand(static_cast<unsigned>(time(nullptr)) + rand());
    return motivationalQuotes[rand() % motivationalQuotes.size()];
}

std::string getRandomWeeklyInsight() {
    srand(static_cast<unsigned>(time(nullptr)) + rand());
    return weeklyInsights[rand() % weeklyInsights.size()];
}

// Function to get current hour (0-23)
int getCurrentHour() {
    time_t now = time(nullptr);
    tm* timeinfo = localtime(&now);
    return timeinfo->tm_hour;
}

// Function to get current day of week (0=Sunday, 6=Saturday)
int getCurrentDayOfWeek() {
    time_t now = time(nullptr);
    tm* timeinfo = localtime(&now);
    return timeinfo->tm_wday;
}

int main() {
    const std::string BOT_TOKEN = "YOUR_BOT_TOKEN_HERE";
    
    // Validate bot token
    if (BOT_TOKEN.empty() || BOT_TOKEN == "YOUR_BOT_TOKEN_HERE") {
        logError("Bot token is not set. Please set BOT_TOKEN environment variable or replace 'YOUR_BOT_TOKEN_HERE'");
        return 1;
    }

    std::unique_ptr<TgBot::Bot> bot;
    
    try {
        // Initialize bot
        bot = std::make_unique<TgBot::Bot>(BOT_TOKEN);
        logInfo("Bot initialized successfully");
    } catch (const TgBot::TgException& e) {
        logError("Failed to initialize bot: " + std::string(e.what()));
        return 1;
    } catch (const std::exception& e) {
        logError("Unexpected error during bot initialization: " + std::string(e.what()));
        return 1;
    }

    // Register /start command handler
    bot->getEvents().onCommand("start", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /start handler");
                return;
            }
            
            int64_t userId = message->from->id;
            
            // Check if user is already subscribed
            bool isNewSubscriber = (subscribedMembers.find(userId) == subscribedMembers.end());
            
            // Add user to subscribers
            subscribedMembers.insert(userId);
            
            std::string response = "Hello! Welcome to the Telegram bot.\n"
                                   "Use /help for available commands.";
            
            if (isNewSubscriber) {
                response += "\n\n🎉 You're now subscribed! You'll receive daily motivational messages!";
                logInfo("New subscriber added: " + std::to_string(userId));
            } else {
                response += "\n\n✅ Welcome back, subscriber!";
                logInfo("Existing subscriber opened bot: " + std::to_string(userId));
            }
            
            bot->getApi().sendMessage(message->chat->id, response);
            logInfo("Sent /start response to chat: " + std::to_string(message->chat->id));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /start handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /start handler: " + std::string(e.what()));
        }
    });

    // Register /help command handler
    bot->getEvents().onCommand("help", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /help handler");
                return;
            }
            
            std::string response = "Available commands:\n"
                                   "/start - Start the bot\n"
                                   "/help - Show this help message\n"
                                   "/info - Get bot information\n"
                                   "/share - Share bot with contacts and groups\n"
                                   "/motivate - Get a motivational message\n"
                                   "/subscribe - Choose subscription type\n"
                                   "/unsubscribe - Stop receiving messages\n"
                                   "/subscribers - Show subscriber count";
            bot->getApi().sendMessage(message->chat->id, response);
            logInfo("Sent /help response to chat: " + std::to_string(message->chat->id));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /help handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /help handler: " + std::string(e.what()));
        }
    });

    // Register /share command handler for affiliation/sharing
    bot->getEvents().onCommand("share", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /share handler");
                return;
            }
            
            // Create inline keyboard with sharing options
            auto keyboard = std::make_shared<TgBot::InlineKeyboardMarkup>();
            std::vector<TgBot::InlineKeyboardButton::Ptr> row;
            
            // Share to contacts button
            auto shareContactsBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            shareContactsBtn->text = "📱 Share to Contacts";
            shareContactsBtn->switchInlineQuery = "Join this amazing Telegram bot!";
            row.push_back(shareContactsBtn);
            
            keyboard->inlineKeyboard.push_back(row);
            
            // Share to groups button
            std::vector<TgBot::InlineKeyboardButton::Ptr> row2;
            auto shareGroupBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            shareGroupBtn->text = "👥 Share to Groups";
            shareGroupBtn->switchInlineQueryCurrentChat = "Check out this bot!";
            row2.push_back(shareGroupBtn);
            
            keyboard->inlineKeyboard.push_back(row2);
            
            // Invite link button (optional)
            std::vector<TgBot::InlineKeyboardButton::Ptr> row3;
            auto inviteBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            inviteBtn->text = "🔗 Get Bot Link";
            inviteBtn->url = "https://t.me/YOUR_BOT_USERNAME_HERE";
            row3.push_back(inviteBtn);
            
            keyboard->inlineKeyboard.push_back(row3);
            
            std::string response = "🌟 Help us grow!\n\n"
                                   "Share this bot with your contacts and groups:\n\n"
                                   "📱 <b>Share to Contacts:</b> Send the bot link to your saved contacts\n"
                                   "👥 <b>Share to Groups:</b> Invite the bot to your favorite groups\n"
                                   "🔗 <b>Get Bot Link:</b> Get the direct link to add this bot\n\n"
                                   "Thank you for helping us grow! 🚀";
            
            bot->getApi().sendMessage(message->chat->id, response, false, 0, keyboard, "HTML");
            logInfo("Sent /share affiliation prompt to chat: " + std::to_string(message->chat->id));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /share handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /share handler: " + std::string(e.what()));
        }
    });

    // Register /motivate command handler
    bot->getEvents().onCommand("motivate", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /motivate handler");
                return;
            }
            
            int64_t userId = message->from->id;
            
            // Add user to subscribers if not already
            bool isNewSubscriber = (subscribedMembers.find(userId) == subscribedMembers.end());
            subscribedMembers.insert(userId);
            
            std::string motivation = getRandomMotivation();
            
            if (isNewSubscriber) {
                motivation += "\n\n✨ You've been added to our subscriber list! You'll receive daily motivation!";
                logInfo("New subscriber from /motivate: " + std::to_string(userId));
            }
            
            bot->getApi().sendMessage(message->chat->id, motivation);
            logInfo("Sent motivational message to chat: " + std::to_string(message->chat->id));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /motivate handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /motivate handler: " + std::string(e.what()));
        }
    });

    // Register /subscribers command handler
    bot->getEvents().onCommand("subscribers", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /subscribers handler");
                return;
            }
            
            std::string response = "📊 <b>Subscriber Statistics</b>\n\n"
                                   "Total Subscribers: <b>" + std::to_string(subscribedMembers.size()) + "</b>\n\n"
                                   "Thank you for being part of our community! 🙏";
            
            bot->getApi().sendMessage(message->chat->id, response, false, 0, nullptr, "HTML");
            logInfo("Sent subscriber count to chat: " + std::to_string(message->chat->id));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /subscribers handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /subscribers handler: " + std::string(e.what()));
        }
    });

    // Register /subscribe command handler
    bot->getEvents().onCommand("subscribe", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /subscribe handler");
                return;
            }
            
            int64_t userId = message->chat->id;
            
            // Create subscription preference keyboard
            auto keyboard = std::make_shared<TgBot::InlineKeyboardMarkup>();
            
            // Daily option
            std::vector<TgBot::InlineKeyboardButton::Ptr> row1;
            auto dailyBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            dailyBtn->text = "📅 Daily Motivation (9 AM)";
            dailyBtn->callbackData = "sub_daily";
            row1.push_back(dailyBtn);
            keyboard->inlineKeyboard.push_back(row1);
            
            // Weekly option
            std::vector<TgBot::InlineKeyboardButton::Ptr> row2;
            auto weeklyBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            weeklyBtn->text = "📆 Weekly Insights (Monday 9 AM)";
            weeklyBtn->callbackData = "sub_weekly";
            row2.push_back(weeklyBtn);
            keyboard->inlineKeyboard.push_back(row2);
            
            // Both option
            std::vector<TgBot::InlineKeyboardButton::Ptr> row3;
            auto bothBtn = std::make_shared<TgBot::InlineKeyboardButton>();
            bothBtn->text = "🎯 Both (Daily + Weekly)";
            bothBtn->callbackData = "sub_both";
            row3.push_back(bothBtn);
            keyboard->inlineKeyboard.push_back(row3);
            
            std::string response = "🎁 <b>Choose Your Subscription</b>\n\n"
                                   "📅 <b>Daily:</b> Get motivated every day at 9 AM\n\n"
                                   "📆 <b>Weekly:</b> Deep insights every Monday at 9 AM\n\n"
                                   "🎯 <b>Both:</b> Daily motivation + Weekly insights\n\n"
                                   "Select an option below:";
            
            bot->getApi().sendMessage(userId, response, false, 0, keyboard, "HTML");
            logInfo("Sent subscription options to chat: " + std::to_string(userId));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /subscribe handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /subscribe handler: " + std::string(e.what()));
        }
    });

    // Register /unsubscribe command handler
    bot->getEvents().onCommand("unsubscribe", [&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat) {
                logWarning("Received invalid message in /unsubscribe handler");
                return;
            }
            
            int64_t userId = message->from->id;
            int64_t chatId = message->chat->id;
            
            subscribedMembers.erase(userId);
            subscriptionPreferences.erase(chatId);
            
            std::string response = "❌ You've been unsubscribed from all messages.\n\n"
                                   "Use /subscribe anytime to re-subscribe! 📨";
            
            bot->getApi().sendMessage(chatId, response);
            logInfo("User unsubscribed: " + std::to_string(userId));
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in /unsubscribe handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in /unsubscribe handler: " + std::string(e.what()));
        }
    });

    // Register generic message handler
    bot->getEvents().onAnyMessage([&bot](TgBot::Message::Ptr message) {
        try {
            if (!message || !message->chat || !message->text) {
                logWarning("Received invalid message in onAnyMessage handler");
                return;
            }
            
            logInfo("Received message from chat " + std::to_string(message->chat->id) + 
                   ": " + message->text);
        } catch (const std::exception& e) {
            logError("Exception in onAnyMessage handler: " + std::string(e.what()));
        }
    });

    // Register callback query handler for subscription preferences
    bot->getEvents().onCallbackQuery([&bot](TgBot::CallbackQuery::Ptr query) {
        try {
            if (!query || !query->data || !query->message || !query->from) {
                logWarning("Received invalid callback query");
                return;
            }
            
            std::string callbackData = query->data;
            int64_t userId = query->from->id;
            int64_t chatId = query->message->chat->id;
            int32_t messageId = query->message->messageId;
            
            std::string subscriptionType;
            std::string confirmMessage;
            
            if (callbackData == "sub_daily") {
                subscriptionType = "daily";
                confirmMessage = "✅ You've subscribed to <b>Daily Motivation</b>!\n\n"
                                "You'll receive motivational messages every day at 9 AM. 📅";
            } else if (callbackData == "sub_weekly") {
                subscriptionType = "weekly";
                confirmMessage = "✅ You've subscribed to <b>Weekly Insights</b>!\n\n"
                                "You'll receive deep insights every Monday at 9 AM. 📆";
            } else if (callbackData == "sub_both") {
                subscriptionType = "both";
                confirmMessage = "✅ You've subscribed to <b>Both Daily & Weekly</b>!\n\n"
                                "Daily motivation at 9 AM + Weekly insights on Mondays! 🎯";
            } else {
                logWarning("Unknown callback data: " + callbackData);
                return;
            }
            
            // Update subscription preferences
            subscriptionPreferences[chatId] = subscriptionType;
            subscribedMembers.insert(userId);
            
            // Edit message to show confirmation
            bot->getApi().editMessageText(confirmMessage, chatId, messageId, nullptr, "HTML");
            
            // Answer callback query
            bot->getApi().answerCallbackQuery(query->id, "Subscription updated!", false);
            
            logInfo("Subscription updated for user " + std::to_string(userId) + 
                   ": " + subscriptionType);
        } catch (const TgBot::TgException& e) {
            logError("TgBot exception in callback handler: " + std::string(e.what()));
        } catch (const std::exception& e) {
            logError("Exception in callback handler: " + std::string(e.what()));
        }
    });

    logInfo("Starting bot polling...");
    
    // Start long polling with error recovery
    try {
        TgBot::TgLongPoll longPoll(*bot);
        int reconnectAttempts = 0;
        const int MAX_RECONNECT_ATTEMPTS = 5;
        int lastDailyHour = -1;
        int lastWeeklyDay = -1;
        
        while (true) {
            try {
                logInfo("Starting long poll");
                longPoll.start();
                reconnectAttempts = 0; // Reset counter on successful poll
                
                // Check for scheduled messages (every iteration)
                int currentHour = getCurrentHour();
                int currentDay = getCurrentDayOfWeek();
                
                // Send daily messages at 9 AM
                if (currentHour == 9 && lastDailyHour != 9) {
                    lastDailyHour = 9;
                    logInfo("Sending daily motivational messages to subscribers...");
                    
                    for (int64_t chatId : subscribedMembers) {
                        try {
                            auto it = subscriptionPreferences.find(chatId);
                            if (it != subscriptionPreferences.end() && 
                                (it->second == "daily" || it->second == "both")) {
                                std::string motivation = getRandomMotivation();
                                bot->getApi().sendMessage(chatId, 
                                    "🌅 <b>Good Morning!</b>\n\n" + motivation, 
                                    false, 0, nullptr, "HTML");
                            }
                        } catch (const std::exception& e) {
                            logWarning("Failed to send daily message to chat " + 
                                      std::to_string(chatId) + ": " + e.what());
                        }
                    }
                } else if (currentHour != 9) {
                    lastDailyHour = -1;
                }
                
                // Send weekly messages on Monday at 9 AM
                if (currentDay == 1 && currentHour == 9 && lastWeeklyDay != 1) {
                    lastWeeklyDay = 1;
                    logInfo("Sending weekly insights to subscribers...");
                    
                    for (int64_t chatId : subscribedMembers) {
                        try {
                            auto it = subscriptionPreferences.find(chatId);
                            if (it != subscriptionPreferences.end() && 
                                (it->second == "weekly" || it->second == "both")) {
                                std::string insight = getRandomWeeklyInsight();
                                bot->getApi().sendMessage(chatId, 
                                    "🌟 <b>Monday Motivation - Start Your Week Strong!</b>\n\n" + insight, 
                                    false, 0, nullptr, "HTML");
                            }
                        } catch (const std::exception& e) {
                            logWarning("Failed to send weekly message to chat " + 
                                      std::to_string(chatId) + ": " + e.what());
                        }
                    }
                } else if (currentDay != 1) {
                    lastWeeklyDay = -1;
                }
                
            } catch (const TgBot::TgException& e) {
                logError("TgBot exception during polling: " + std::string(e.what()));
                reconnectAttempts++;
                
                if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    logError("Max reconnection attempts reached. Shutting down.");
                    break;
                }
                
                int backoffSeconds = reconnectAttempts * 5; // Exponential backoff
                logWarning("Attempting to reconnect in " + std::to_string(backoffSeconds) + " seconds...");
                std::this_thread::sleep_for(std::chrono::seconds(backoffSeconds));
            } catch (const std::exception& e) {
                logError("Unexpected exception during polling: " + std::string(e.what()));
                reconnectAttempts++;
                
                if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    logError("Max reconnection attempts reached. Shutting down.");
                    break;
                }
                
                int backoffSeconds = reconnectAttempts * 5;
                logWarning("Attempting to reconnect in " + std::to_string(backoffSeconds) + " seconds...");
                std::this_thread::sleep_for(std::chrono::seconds(backoffSeconds));
            }
        }
    } catch (const TgBot::TgException& e) {
        logError("TgBot exception creating long poll: " + std::string(e.what()));
        return 1;
    } catch (const std::exception& e) {
        logError("Unexpected error: " + std::string(e.what()));
        return 1;
    }

    logInfo("Bot shutdown complete");
    return 0;
}

// Note: Replace "YOUR_BOT_TOKEN_HERE" with your actual Telegram bot token. Make sure to handle exceptions and errors as needed for a production-level bot.     
// Compile with C++17 standard and link against tgbot-cpp and its dependencies.
// Example compilation command (adjust paths as necessary):
// g++ -std=c++17 -o telegram-bot main.cpp -ltgbot -lboost_system -lcurl -lssl -lcrypto -lpthread

// Ensure you have set up your development environment with the required libraries and dependencies for tgbot-cpp.

// This code provides a basic structure for a Telegram bot using the tgbot-cpp library.



