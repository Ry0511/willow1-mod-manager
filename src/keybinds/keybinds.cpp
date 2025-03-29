//
// Date       : 19/11/2024
// Project    : willow_mod_manager
// Author     : -Ry
//

#include "pyunrealsdk/pch.h"
#include <pyunrealsdk/hooks.h>
#include "pyunrealsdk/static_py_object.h"
#include "pyunrealsdk/unreal_bindings/uenum.h"

#include "unrealsdk/hook_manager.h"
#include "unrealsdk/memory.h"
#include "unrealsdk/unreal/class_name.h"
#include "unrealsdk/unreal/classes/properties/uboolproperty.h"
#include "unrealsdk/unreal/classes/properties/ubyteproperty.h"
#include "unrealsdk/unreal/find_class.h"
#include "unrealsdk/unrealsdk.h"

namespace keybinds {

// ############################################################################//
//  | DEFINES |
// ############################################################################//

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
    bool is_gameplay{};
    bool is_any_key{};
};

pyunrealsdk::StaticPyObject input_event_enum = pyunrealsdk::unreal::enum_as_py_enum(
    validate_type<UEnum>(unrealsdk::find_object(L"Enum", L"Core.Object.EInputEvent"))
);

const FName ANY_KEY{0, 0};
std::unordered_multimap<FName, std::shared_ptr<KeybindInfo>> callback_map{};

// ############################################################################//
//  | DISPATCH KEY EVENTS |
// ############################################################################//

void dispatch_key_events(const FName& key, EInputEvent event, bool is_gameplay) noexcept {
    using ElemType = std::shared_ptr<KeybindInfo>;
    std::vector<ElemType> keybinds{};

    // Copy into vector
    auto copy_keybinds = [&keybinds, is_gameplay, event](const FName& key) {
        auto [it, end] = callback_map.equal_range(key);
        for (; it != end; ++it) {
            const ElemType& info = it->second;

            if (is_gameplay != info->is_gameplay) {
                continue;
            }
            if (info->filter.has_value() && *info->filter != event) {
                continue;
            }

            keybinds.push_back(it->second);
        }
    };
    copy_keybinds(ANY_KEY);
    copy_keybinds(key);

    // Skip
    if (keybinds.empty()) {
        return;
    }

    const py::gil_scoped_acquire gil{};
    py::object block_signal{};
    py::object event_type;
    py::object key_str;
    for (const std::shared_ptr<KeybindInfo>& info : keybinds) {
        py::list args{};

        // If there is an event filter append the event arg
        if (!info->filter.has_value()) {
            if (!event_type) {
                event_type = input_event_enum(event);
            }
            args.append(event_type);
        }

        // If any key then append the key string
        if (info->is_any_key) {
            if (!key_str) {
                key_str = py::str(std::string(key));
            }
            args.append(key_str);
        }

        // Call the callback
        auto ret = info->callback(*args);

        // This only skips the callbacks in this chain not the games callbacks
        if (pyunrealsdk::hooks::is_block_sentinel(ret)) {
            return;
        }
    }
}

// ############################################################################//
//  | INPUT HOOK |
// ############################################################################//

namespace {

typedef void*(__fastcall* on_input_event_func)(
    UObject* ecx,
    void* edx,
    PropTraits<UIntProperty>::Value controller,
    PropTraits<UNameProperty>::Value key,
    PropTraits<UByteProperty>::Value event,
    PropTraits<UFloatProperty>::Value amount_depressed,
    PropTraits<UBoolProperty>::Value is_gamepad
);

on_input_event_func input_func_ptr{nullptr};

void* __fastcall hook_input_func(
    UObject* ecx,
    void* edx,
    PropTraits<UIntProperty>::Value controller,
    PropTraits<UNameProperty>::Value key,
    PropTraits<UByteProperty>::Value event,
    PropTraits<UFloatProperty>::Value amount_depressed,
    PropTraits<UBoolProperty>::Value is_gamepad
) {
    // NOTE: We only discern if we are in gameplay or not since WillowConsole runs everywhere
    //  (except loading screens).
    static UObject* gameplay_input_class = unreal::find_class(L"WillowGame.WillowUIInteraction");
    // static UObject* ui_input_class = unreal::find_class(L"WillowGame.WillowConsole");

    bool is_gameplay = ecx->Class == gameplay_input_class;
    dispatch_key_events(key, event, is_gameplay);

    // idk what this returns; seems to be 0x0 most of the time
    return input_func_ptr(ecx, edx, controller, key, event, amount_depressed, is_gamepad);
}

// probably not a bitcoin miner
Pattern<80> INPUT_FUN_SIG{
    "83 EC 1C"
    "8B 44 24 20"
    "8B 54 24 24"
    "89 04 24"
    "8B 44 24 28"
    "F3 0F 10 44 24 30"
    "89 44 24 08"
    "33 C0"
    "39 44 24 34"
    "6A 00"
    "0F 95 C0"
    "89 54 24 08"
    "8A 54 24 30"
    "88 54 24 10"
    "8B 11"
    "8B 92 F4 00 00 00"
    "C7 44 24 1C 00 00 00 00"
    "89 44 24 18"
    "8D 44 24 04"
    "50"
    "8D 41 3C"
    "50"
};

}  // namespace
}  // namespace keybinds

// ############################################################################//
//  | PYBIND |
// ############################################################################//

PYBIND11_MODULE(keybinds, m) {
    using namespace unrealsdk::unreal;
    using namespace unrealsdk::memory;
    using namespace keybinds;

    detour(
        keybinds::INPUT_FUN_SIG,
        keybinds::hook_input_func,
        &keybinds::input_func_ptr,
        "__keybinds_hook_input_func"
    );

    m.def(
        "register_keybind",
        [](const std::optional<FName>& key,
           const std::optional<EInputEvent>& filter,
           bool is_gameplay_bind,
           const py::object& callback) -> void* {
        using keybinds::KeybindInfo;
        auto it = keybinds::callback_map.emplace(
            std::make_pair(
                key.value_or(ANY_KEY),
                std::make_shared<KeybindInfo>(callback, filter, is_gameplay_bind, !key.has_value())
            )
        );
        return it->second.get();
    },
        "key"_a,
        "filter"_a,
        "is_gameplay_bind"_a,
        "callback"_a
    );

    m.def("deregister_keybind", [](void* handle) {
        std::erase_if(keybinds::callback_map, [handle](const auto& entry) -> bool {
            const auto& [_, info] = entry;
            return handle == info.get();
        });
    }, "handle"_a);

    m.def("deregister_by_key", [](const FName& key) {
        std::erase_if(keybinds::callback_map, [key](const auto& entry) {
            const auto& [key_in_map, _] = entry;
            return key == key_in_map;
        });
    }, "key"_a);

    m.def("deregister_all", []() { keybinds::callback_map.clear(); });
}