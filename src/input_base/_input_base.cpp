//
// Date       : 19/11/2024
// Project    : willow_mod_manager
// Author     : -Ry
//

#include "pyunrealsdk/pch.h"
#include "pyunrealsdk/static_py_object.h"
#include "pyunrealsdk/unreal_bindings/uenum.h"

#include "unrealsdk/memory.h"
#include "unrealsdk/unrealsdk.h"
#include "unrealsdk/hook_manager.h"
#include "unrealsdk/unreal/class_name.h"
#include "unrealsdk/unreal/classes/properties/uboolproperty.h"
#include "unrealsdk/unreal/classes/properties/ubyteproperty.h"

namespace keybinds {

using namespace unrealsdk;
using namespace unrealsdk::unreal;
using namespace unrealsdk::memory;

using EInputEvent = PropTraits<UByteProperty>::Value;
constexpr EInputEvent IE_Pressed = 0;
constexpr EInputEvent IE_Released = 1;
constexpr EInputEvent IE_Repeat = 2;
constexpr EInputEvent IE_DoubleClick = 3;
constexpr EInputEvent IE_Axis = 4;
constexpr EInputEvent IE_MAX = 5;

struct PY_OBJECT_VISIBILITY KeybindInfo {
    pyunrealsdk::StaticPyObject callback;
    std::optional<EInputEvent> filter;
};

pyunrealsdk::StaticPyObject input_event_enum = pyunrealsdk::unreal::enum_as_py_enum(
        validate_type<UEnum>(
                unrealsdk::find_object(
                        L"Enum",
                        L"Core.Object.EInputEvent"
                )
        )
);

std::unordered_multimap<FName, std::unique_ptr<KeybindInfo>> callback_map{};

void dispatch_key_events(const FName& key, EInputEvent event) noexcept {
    const auto& [begin, end] = callback_map.equal_range(key);

    const py::gil_scoped_acquire gil{};
    for (auto it = begin; it != end; ++it) {
        const KeybindInfo& info = *it->second;
        if (!info.filter.has_value() || (*info.filter) == event) {
            info.callback(event);
        }
    }
}

bool hook_on_gameplay_input(hook_manager::Details& hook) {
    FName key = hook.args->get<UNameProperty>(L"Key"_fn);
    EInputEvent event = hook.args->get<UByteProperty>(L"Event"_fn);
    keybinds::dispatch_key_events(key, event);
    return false;
}

namespace {

typedef void* (__fastcall* on_input_event_func)(
        UObject* ecx,
        void* edx,
        PropTraits<UIntProperty>::Value controller,
        PropTraits<UNameProperty>::Value key,
        PropTraits<UByteProperty>::Value event,
        PropTraits<UFloatProperty>::Value amount_depressed,
        PropTraits<UBoolProperty>::Value is_gamepad
);

on_input_event_func input_func_ptr{nullptr};

// int ControllerId,
// name Key,
// Object.EInputEvent Event,
// optional float AmountDepressed = 1.0000000,
// optional bool bGamepad = false
static void* __fastcall hook_input_func(
        UObject* ecx,
        void* edx,
        PropTraits<UIntProperty>::Value controller,
        PropTraits<UNameProperty>::Value key,
        PropTraits<UByteProperty>::Value event,
        PropTraits<UFloatProperty>::Value amount_depressed,
        PropTraits<UBoolProperty>::Value is_gamepad
) {
    // - NOTE - above means in the stack frame above this or below you if you're egotistical
    // I would prefer to hook the function just above this however the function is very sensitive
    // to stack changes and always ends up crashing. The best I could get was making it not crash on
    // one call and that was with __declspec(naked) and inline assembly.
    //
    // For future reference the function above (0x009355B1) has a signature equal to:
    // ; return 0x01 is a return constant probably a bool?
    // int __thiscall(void*   this,
    //                int32_t param_1, // Unused
    //                int32_t param_2, // Unused
    //                int32_t controller,
    //                FName   key,     // index, number
    //                uint8_t event,   // +3 padding most likely
    //                float   amount_depressed)
    //

    static std::unordered_map<FName, EInputEvent> previous_event_map{};

    // Don't fire multiple events of the same type (unless its a repeat event)
    if (previous_event_map.contains(key)
        && event != IE_Repeat
        && previous_event_map[key] == event) {
        return input_func_ptr(
                ecx,
                edx,
                controller,
                key,
                event,
                amount_depressed,
                is_gamepad
        );
    }
    previous_event_map[key] = static_cast<EInputEvent>(event);
    dispatch_key_events(key, static_cast<EInputEvent>(event));

    return input_func_ptr(ecx, edx, controller, key, event, amount_depressed, is_gamepad);
}

Pattern<80> INPUT_FUN_SIG{ // probably not a bitcoin miner
        "83 EC 1C 8B 44 24 20 8B 54 24 24 89 04 24 8B 44 24 28 F3 0F 10 44 24 30 89 44 24 08 33"
        "C0 39 44 24 34 6A 00 0F 95 C0 89 54 24 08 8A 54 24 30 88 54 24 10 8B 11 8B 92 F4 00 00"
        "00 C7 44 24 1C 00 00 00 00 89 44 24 18 8D 44 24 04 50 8D 41 3C 50"
};

}
} // keybinds


PYBIND11_MODULE(_input_base, m) {

    using namespace unrealsdk::unreal;
    using namespace unrealsdk::memory;
    using namespace keybinds;

    detour(
            keybinds::INPUT_FUN_SIG,
            keybinds::hook_input_func,
            &keybinds::input_func_ptr,
            "InputFunc::InputEvent"
    );

    m.def(
            "register_keybind",
            [](
                    const FName& key,
                    const std::optional<EInputEvent>& filter,
                    const py::object& callback
            ) -> void* {
                using keybinds::KeybindInfo;
                auto it = keybinds::callback_map.emplace(
                        std::make_pair(key, std::make_unique<KeybindInfo>(callback, filter))
                );
                return it->second.get();
            },
            "key"_a,
            "filter"_a,
            "callback"_a
    );

    m.def(
            "deregister_keybind",
            [](void* handle) {
                std::erase_if(
                        keybinds::callback_map,
                        [handle](const auto& entry) -> bool {
                            const auto& [_, info] = entry;
                            return handle == info.get();
                        }
                );
            },
            "handle"_a
    );

    m.def(
            "deregister_by_key",
            [](const FName& key) {
                std::erase_if(
                        keybinds::callback_map, [key](const auto& entry) {
                            const auto& [key_in_map, _] = entry;
                            return key == key_in_map;
                        }
                );
            },
            "key"_a
    );

    m.def("deregister_all", []() { keybinds::callback_map.clear(); });

}