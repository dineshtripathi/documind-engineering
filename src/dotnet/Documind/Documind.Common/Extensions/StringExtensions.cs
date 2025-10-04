namespace Documind.Common.Extensions;

/// <summary>
/// Extension methods for strings
/// </summary>
public static class StringExtensions
{
    /// <summary>
    /// Checks if a string is null, empty, or contains only whitespace
    /// </summary>
    public static bool IsNullOrWhiteSpace(this string? value)
    {
        return string.IsNullOrWhiteSpace(value);
    }

    /// <summary>
    /// Checks if a string has actual content (not null, empty, or whitespace)
    /// </summary>
    public static bool HasValue(this string? value)
    {
        return !string.IsNullOrWhiteSpace(value);
    }

    /// <summary>
    /// Returns the string if it has value, otherwise returns the default value
    /// </summary>
    public static string OrDefault(this string? value, string defaultValue = "")
    {
        return value.HasValue() ? value! : defaultValue;
    }

    /// <summary>
    /// Truncates a string to the specified maximum length
    /// </summary>
    public static string Truncate(this string value, int maxLength, string suffix = "...")
    {
        if (string.IsNullOrEmpty(value) || value.Length <= maxLength)
            return value;

        return value[..(maxLength - suffix.Length)] + suffix;
    }
}
